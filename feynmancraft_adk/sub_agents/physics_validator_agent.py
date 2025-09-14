# Copyright 2024-2025 The FeynmanCraft ADK Project Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Physics Validator Agent for FeynmanCraft ADK.

This agent acts as a coordinator for physics validation. It receives a physics process,
finds relevant rules from a JSON database via semantic search, and orchestrates validation.
For rules requiring computation, it delegates to specialized tools.

Enhanced with ParticlePhysics MCP Server tools for comprehensive particle data validation.

This agent has been refactored to use the centralized tools module for all data loading,
embedding management, search functionality, and physics validation tools.
"""

import logging
from typing import Dict, List, Any

from google.adk.agents import Agent

from ..models import PHYSICS_VALIDATOR_MODEL
from .physics_validator_agent_prompt import PROMPT as PHYSICS_VALIDATOR_AGENT_PROMPT

# Import physics search functionality from tools
from ..tools.physics.search import (
    search_physics_rules,
    search_rules_by_particles,
    search_rules_by_process,
    validate_process_against_rules
)

# Import physics tools for enhanced particle validation
from ..tools.physics import (
    search_particle,
    get_particle_properties,
    validate_quantum_numbers,
    get_branching_fractions,
    compare_particles,
    convert_units,
    check_particle_properties,
)

# Import natural language physics parsing
from ..tools.physics.physics_tools import (
    parse_natural_language_physics
)

# Import agent search integration tools for comprehensive particle physics validation
from ..integrations import (
    enhanced_agent_search_with_particle_info,
    quick_particle_validation_for_agent,
    get_diagram_relevant_particle_info,
)

# Import experimental MCP tools
from experimental.particlephysics_mcp import (
    search_particle_experimental,
    list_decays_experimental
)

# Import experimental physics tools for enhanced validation
from ..tools.physics.experimental_physics_tools import (
    search_particle_experimental_enhanced,
    get_particle_decays_experimental,
    validate_particle_experimental,
    search_particles_for_agent,
    get_particle_interaction_info
)

# Import agent search integration for comprehensive particle analysis


logger = logging.getLogger(__name__)


# --- Wrapper functions for agent tools ---

async def search_physics_rules_wrapper(query: str) -> List[Dict[str, Any]]:
    """
    Wrapper for search_physics_rules with default parameters.
    
    Args:
        query: Natural language query about physics rules
        
    Returns:
        List of relevant physics rules
    """
    try:
        return await search_physics_rules(query, top_k=5)
    except Exception as e:
        logger.error(f"Error in search_physics_rules_wrapper: {e}")
        return [{"error": f"Physics rules search failed: {str(e)}"}]


def search_rules_by_particles_wrapper(particles: str) -> List[Dict[str, Any]]:
    """
    Wrapper for searching rules by particles.
    
    Args:
        particles: Comma-separated list of particle names
        
    Returns:
        List of relevant physics rules
    """
    try:
        particle_list = [p.strip() for p in particles.split(',')]
        return search_rules_by_particles(particle_list, top_k=10)
    except Exception as e:
        logger.error(f"Error in search_rules_by_particles_wrapper: {e}")
        return [{"error": f"Particle rules search failed: {str(e)}"}]


def search_rules_by_process_wrapper(process_description: str) -> List[Dict[str, Any]]:
    """
    Wrapper for searching rules by process description.
    
    Args:
        process_description: Description of the physics process
        
    Returns:
        List of relevant physics rules
    """
    try:
        return search_rules_by_process(process_description, top_k=5)
    except Exception as e:
        logger.error(f"Error in search_rules_by_process_wrapper: {e}")
        return [{"error": f"Process rules search failed: {str(e)}"}]


def validate_process_wrapper(process_description: str, particles: str) -> Dict[str, Any]:
    """
    Wrapper for comprehensive process validation.
    
    Args:
        process_description: Description of the physics process
        particles: Comma-separated list of particles involved
        
    Returns:
        Validation result
    """
    try:
        particle_list = [p.strip() for p in particles.split(',')]
        return validate_process_against_rules(process_description, particle_list)
    except Exception as e:
        logger.error(f"Error in validate_process_wrapper: {e}")
        return {
            "process": process_description,
            "particles": particles,
            "error": str(e),
            "validation_status": "failed"
        }


def parse_natural_language_physics_wrapper(query: str) -> Dict[str, Any]:
    """
    Wrapper for parsing natural language physics queries.
    
    Args:
        query: Natural language physics query
        
    Returns:
        Parsed physics information
    """
    try:
        result = parse_natural_language_physics(query)
        return result
    except Exception as e:
        logger.error(f"Error in parse_natural_language_physics_wrapper: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'original_query': query
        }


# --- Experimental MCP Tool Wrappers ---
# These wrappers handle async calls for experimental MCP tools

async def search_particle_experimental_wrapper(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Wrapper for experimental MCP particle search."""
    try:
        return await search_particle_experimental(query)
    except Exception as e:
        logger.error(f"Experimental MCP search_particle failed: {e}")
        return {"error": str(e), "status": "failed"}


async def list_decays_experimental_wrapper(particle_name: str) -> Dict[str, Any]:
    """Wrapper for experimental MCP particle decay listing."""
    try:
        return await list_decays_experimental(particle_name)
    except Exception as e:
        logger.error(f"Experimental MCP list_decays failed: {e}")
        return {"error": str(e), "status": "failed"}


async def search_particle_mcp_wrapper(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Wrapper for experimental MCP particle search."""
    try:
        return await search_particle_experimental(query)
    except Exception as e:
        logger.error(f"Experimental MCP search_particle failed: {e}")
        return {"error": str(e), "status": "failed"}


async def get_particle_properties_mcp_wrapper(particle_name: str, units_preference: str = "GeV") -> Dict[str, Any]:
    """Wrapper for experimental MCP particle properties."""
    try:
        return await search_particle_experimental(particle_name)
    except Exception as e:
        logger.error(f"Experimental get_particle_properties failed: {e}")
        return {"error": str(e), "status": "failed"}


async def validate_quantum_numbers_mcp_wrapper(particle_name: str) -> Dict[str, Any]:
    """Wrapper for experimental particle search to provide quantum number validation."""
    try:
        result = await search_particle_experimental(particle_name)
        # The experimental server provides particle information that can be used for validation
        if "error" in result:
            return {"valid": False, "error": result["error"]}
        return {"valid": True, "particle_info": result}
    except Exception as e:
        logger.error(f"Experimental quantum number validation failed: {e}")
        return {"error": str(e), "status": "failed"}


async def get_branching_fractions_mcp_wrapper(particle_name: str, limit: int = 10) -> Dict[str, Any]:
    """Wrapper for experimental MCP branching fractions using decay list."""
    try:
        return await list_decays_experimental(particle_name)
    except Exception as e:
        logger.error(f"Experimental get_branching_fractions failed: {e}")
        return {"error": str(e), "status": "failed"}


async def compare_particles_mcp_wrapper(particle_names: str, properties: str = "mass,charge,spin") -> Dict[str, Any]:
    """Wrapper for experimental particle comparison."""
    try:
        particle_list = [p.strip() for p in particle_names.split(',')]
        results = []
        for particle in particle_list:
            result = await search_particle_experimental(particle)
            results.append({"particle": particle, "info": result})
        return {"comparison": results}
    except Exception as e:
        logger.error(f"Experimental compare_particles failed: {e}")
        return {"error": str(e), "status": "failed"}


async def convert_units_mcp_wrapper(value: float, from_units: str, to_units: str) -> Dict[str, Any]:
    """Wrapper for unit conversion (simplified for experimental version)."""
    try:
        # Basic unit conversion logic - can be enhanced later
        return {"converted_value": value, "from_units": from_units, "to_units": to_units, "note": "Basic conversion"}
    except Exception as e:
        logger.error(f"Unit conversion failed: {e}")
        return {"error": str(e), "status": "failed"}


async def check_particle_properties_mcp_wrapper(particle_name: str) -> Dict[str, Any]:
    """Wrapper for experimental particle property check."""
    try:
        return await search_particle_experimental(particle_name)
    except Exception as e:
        logger.error(f"Experimental check_particle_properties failed: {e}")
        return {"error": str(e), "status": "failed"}


# --- Agent Search Integration Wrappers ---

async def enhanced_agent_search_wrapper(query: str, particles: str = "", max_kb_results: int = 5) -> Dict[str, Any]:
    """Wrapper for enhanced agent search with particle info."""
    try:
        particle_list = [p.strip() for p in particles.split(',')] if particles else None
        return await enhanced_agent_search_with_particle_info(query, particle_list, max_kb_results)
    except Exception as e:
        logger.error(f"Enhanced agent search failed: {e}")
        return {"error": str(e), "status": "failed"}


async def quick_particle_validation_wrapper(particles: str) -> Dict[str, Any]:
    """Wrapper for quick particle validation."""
    try:
        particle_list = [p.strip() for p in particles.split(',')]
        return await quick_particle_validation_for_agent(particle_list)
    except Exception as e:
        logger.error(f"Quick particle validation failed: {e}")
        return {"error": str(e), "status": "failed"}


async def get_diagram_particle_info_wrapper(particles: str) -> Dict[str, Any]:
    """Wrapper for diagram-relevant particle info."""
    try:
        particle_list = [p.strip() for p in particles.split(',')]
        return await get_diagram_relevant_particle_info(particle_list)
    except Exception as e:
        logger.error(f"Diagram particle info extraction failed: {e}")
        return {"error": str(e), "status": "failed"}


async def get_particle_decays_experimental_wrapper(particle_name: str, limit: int = 10) -> Dict[str, Any]:
    """Wrapper for experimental particle decay analysis."""
    try:
        return await get_particle_decays_experimental(particle_name, limit=limit)
    except Exception as e:
        logger.error(f"Experimental decay analysis failed: {e}")
        return {"error": str(e), "status": "failed"}


async def validate_particle_experimental_wrapper(particle_name: str) -> Dict[str, Any]:
    """Wrapper for experimental particle validation."""
    try:
        return await validate_particle_experimental(particle_name)
    except Exception as e:
        logger.error(f"Experimental particle validation failed: {e}")
        return {"error": str(e), "status": "failed"}


async def search_particles_for_agent_wrapper(particles_str: str) -> Dict[str, Any]:
    """Wrapper for agent-optimized particle search with multiple particles."""
    try:
        particles = [p.strip() for p in particles_str.split(',')]
        return await search_particles_for_agent(particles)
    except Exception as e:
        logger.error(f"Agent particle search failed: {e}")
        return {"error": str(e), "status": "failed"}


async def get_particle_interaction_info_wrapper(particles_str: str) -> Dict[str, Any]:
    """Wrapper for particle interaction information analysis."""
    try:
        particles = [p.strip() for p in particles_str.split(',')]
        return await get_particle_interaction_info(particles)
    except Exception as e:
        logger.error(f"Particle interaction info failed: {e}")
        return {"error": str(e), "status": "failed"}


# --- Agent Search Integration Wrappers ---

async def enhanced_agent_search_wrapper(query: str, particles_str: str = "", max_kb_results: int = 5, max_physics_rules: int = 5) -> Dict[str, Any]:
    """Wrapper for enhanced agent search with particle information integration."""
    try:
        particles = [p.strip() for p in particles_str.split(',') if p.strip()] if particles_str else None
        return await enhanced_agent_search_with_particle_info(
            query=query,
            particles=particles,
            max_kb_results=max_kb_results,
            max_physics_rules=max_physics_rules
        )
    except Exception as e:
        logger.error(f"Enhanced agent search failed: {e}")
        return {"error": str(e), "status": "failed"}


async def quick_particle_validation_wrapper(particles_str: str) -> Dict[str, Any]:
    """Wrapper for quick particle validation optimized for agent workflows."""
    try:
        particles = [p.strip() for p in particles_str.split(',') if p.strip()]
        return await quick_particle_validation_for_agent(particles)
    except Exception as e:
        logger.error(f"Quick particle validation failed: {e}")
        return {"error": str(e), "status": "failed"}


async def get_diagram_particle_info_wrapper(particles_str: str) -> Dict[str, Any]:
    """Wrapper for getting diagram-relevant particle information."""
    try:
        particles = [p.strip() for p in particles_str.split(',') if p.strip()]
        return await get_diagram_relevant_particle_info(particles)
    except Exception as e:
        logger.error(f"Diagram particle info extraction failed: {e}")
        return {"error": str(e), "status": "failed"}


# --- Agent Definition ---

PhysicsValidatorAgent = Agent(
    model=PHYSICS_VALIDATOR_MODEL,  # Use gemini-2.5-pro for complex physics validation
    name="physics_validator_agent",
    description="Validates physics processes using comprehensive particle physics tools, MCP tools, and natural language processing. Uses centralized tools for all validation operations.",
    instruction=PHYSICS_VALIDATOR_AGENT_PROMPT,
    output_key="physics_validation_report",  # State management: outputs to state.physics_validation_report
    tools=[
        # Physics rules search tools
        search_physics_rules_wrapper,
        search_rules_by_particles_wrapper,
        search_rules_by_process_wrapper,
        validate_process_wrapper,
        
        # Internal physics tools (these already use MCP internally)
        search_particle,
        get_particle_properties,
        validate_quantum_numbers,
        get_branching_fractions,
        compare_particles,
        convert_units,
        check_particle_properties,
        
        # Experimental MCP physics tools with proper wrappers
        search_particle_mcp_wrapper,
        get_particle_properties_mcp_wrapper,
        validate_quantum_numbers_mcp_wrapper,
        get_branching_fractions_mcp_wrapper,
        compare_particles_mcp_wrapper,
        convert_units_mcp_wrapper,
        check_particle_properties_mcp_wrapper,
        
        # Experimental physics tools with enhanced capabilities
        search_particle_experimental_wrapper,
        list_decays_experimental_wrapper,
        
        # Agent search integration tools (primary particle portal for agents)
        enhanced_agent_search_wrapper,
        quick_particle_validation_wrapper,
        get_diagram_particle_info_wrapper,
        
        # Natural language processing tools
        parse_natural_language_physics_wrapper,
    ],
)