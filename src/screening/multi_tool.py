"""
Multi-tool screening pipeline for variant detection.
Implements BLASTP, HMMER, and other screening methods.
"""

import subprocess
import tempfile
import os
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ScreeningResult:
    """Container for screening results"""

    def __init__(self, tool_name: str, evaded: bool, hits: List[Dict], threshold: float):
        self.tool_name = tool_name
        self.evaded = evaded
        self.hits = hits
        self.threshold = threshold
        self.best_hit = hits[0] if hits else None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'tool': self.tool_name,
            'evaded': self.evaded,
            'num_hits': len(self.hits),
            'threshold': self.threshold,
            'best_hit': self.best_hit,
            'all_hits': self.hits
        }

class BlastpScreener:
    """BLASTP screening tool"""

    def __init__(self, database_path: str):
        self.database_path = database_path

    def screen(self, sequence: str, variant_id: str, evalue_threshold: float = 1e-5) -> ScreeningResult:
        """Screen sequence against BLASTP database"""

        # Create temporary query file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.fasta') as query_file:
            query_record = SeqRecord(Seq(sequence), id=variant_id, description="Screening query")
            SeqIO.write([query_record], query_file.name, "fasta")
            query_path = query_file.name

        # Create temporary results file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tsv') as result_file:
            result_path = result_file.name

        cmd = (f"blastp -query {query_path} -db {self.database_path} -out {result_path} "
               f"-outfmt '6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore' "
               f"-evalue {evalue_threshold} -max_target_seqs 5")

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)

            # Parse results
            hits = []
            if os.path.getsize(result_path) > 0:
                with open(result_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split('\t')
                            hits.append({
                                'target_id': parts[1],
                                'percent_identity': float(parts[2]),
                                'alignment_length': int(parts[3]),
                                'evalue': float(parts[10]),
                                'bitscore': float(parts[11])
                            })

            # Clean up temporary files
            os.unlink(query_path)
            os.unlink(result_path)

            # Determine evasion status
            evaded = len(hits) == 0

            return ScreeningResult(
                tool_name='blastp',
                evaded=evaded,
                hits=hits,
                threshold=evalue_threshold
            )

        except subprocess.CalledProcessError as e:
            logger.error(f"BLASTP screening failed: {e}")
            # Clean up on error
            if os.path.exists(query_path):
                os.unlink(query_path)
            if os.path.exists(result_path):
                os.unlink(result_path)

            return ScreeningResult(
                tool_name='blastp',
                evaded=False,  # Conservative: assume detected on error
                hits=[],
                threshold=evalue_threshold
            )

class MultiToolScreener:
    """Multi-tool screening pipeline"""

    def __init__(self, database_path: str):
        self.blastp_screener = BlastpScreener(database_path)

    def screen_comprehensive(self, sequence: str, variant_id: str,
                           evalue_thresholds: Optional[List[float]] = None) -> Dict[str, ScreeningResult]:
        """
        Screen sequence with multiple tools and thresholds.

        Args:
            sequence: Protein sequence to screen
            variant_id: Unique identifier for the variant
            evalue_thresholds: List of E-value thresholds to test

        Returns:
            Dictionary mapping tool_threshold -> ScreeningResult
        """
        if evalue_thresholds is None:
            evalue_thresholds = [1e-3, 1e-5, 1e-7, 1e-10]

        results = {}

        # Run BLASTP with multiple thresholds
        for threshold in evalue_thresholds:
            tool_key = f"blastp_{threshold:.0e}"
            results[tool_key] = self.blastp_screener.screen(sequence, variant_id, threshold)

        return results

    def assess_joint_evasion(self, screening_results: Dict[str, ScreeningResult],
                            required_tools: Optional[List[str]] = None) -> bool:
        """
        Assess if variant evades all required screening tools.

        Args:
            screening_results: Results from screen_comprehensive
            required_tools: List of required tools (default: strict BLASTP thresholds)

        Returns:
            True if variant evades all required tools
        """
        if required_tools is None:
            # Default: must evade both 1e-5 and 1e-7 BLASTP thresholds
            required_tools = ['blastp_1e-05', 'blastp_1e-07']

        for tool in required_tools:
            if tool not in screening_results:
                logger.warning(f"Required tool {tool} not found in screening results")
                return False

            if not screening_results[tool].evaded:
                return False

        return True

def create_blast_database(sequences: Dict[str, str], output_path: str) -> str:
    """
    Create BLAST database from protein sequences.

    Args:
        sequences: Dict mapping protein_id -> sequence
        output_path: Output path for database (without extension)

    Returns:
        Database path
    """
    fasta_path = f"{output_path}.fasta"

    # Write sequences to FASTA file
    records = []
    for protein_id, sequence in sequences.items():
        record = SeqRecord(
            Seq(sequence),
            id=protein_id,
            description=f"Protein {protein_id}"
        )
        records.append(record)

    SeqIO.write(records, fasta_path, "fasta")

    # Create BLAST database
    cmd = f"makeblastdb -in {fasta_path} -dbtype prot -out {output_path}"
    subprocess.run(cmd, shell=True, check=True)

    logger.info(f"Created BLAST database: {output_path}")
    return output_path

def load_screening_database(database_path: str) -> MultiToolScreener:
    """
    Load screening database and return screener instance.

    Args:
        database_path: Path to BLAST database

    Returns:
        MultiToolScreener instance
    """
    return MultiToolScreener(database_path)